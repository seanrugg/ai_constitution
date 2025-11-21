import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { motion } from "framer-motion";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

// -------------------------
// Validation Schema
// -------------------------
const schema = z.object({
  title: z.string().min(3, "Title must be at least 3 characters"),
  summary: z.string().min(10, "Summary must be at least 10 characters"),
  proposal: z.string().min(20, "Proposal text must be at least 20 characters"),
  author: z.string().min(2, "Author name required"),
  email: z.string().email("Invalid email address"),
});

export default function ProposalWizard() {
  const [step, setStep] = useState(1);
  const [darkMode, setDarkMode] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({ resolver: zodResolver(schema) });

  // -------------------------
  // API Submit Handler
  // -------------------------
  const onSubmit = async (data) => {
    try {
      const res = await fetch("/api/proposals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) throw new Error("Submission failed");
      alert("Proposal submitted successfully!");
    } catch (err) {
      alert("Error submitting proposal: " + err.message);
    }
  };

  const nextStep = () => setStep((s) => Math.min(s + 1, 3));
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  return (
    <div className={`${darkMode ? "dark bg-gray-900 text-gray-100" : "bg-gray-50 text-gray-900"} min-h-screen p-10 transition-colors`}>
      <div className="flex justify-end mb-4 gap-2 items-center">
        <span className="text-sm">Dark Mode</span>
        <Switch checked={darkMode} onCheckedChange={setDarkMode} />
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        <Card className="max-w-2xl mx-auto shadow-xl rounded-2xl">
          <CardContent className="p-8 space-y-6">
            <h1 className="text-3xl font-bold mb-2">Proposal Submission Wizard</h1>
            <p className="text-gray-500 dark:text-gray-400">Step {step} of 3</p>

            <form onSubmit={handleSubmit(onSubmit)}>
              {/* ---------------- Step 1 ---------------- */}
              {step === 1 && (
                <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="space-y-4">
                  <div>
                    <label className="font-semibold">Title</label>
                    <Input {...register("title")} />
                    {errors.title && <p className="text-red-500 text-sm">{errors.title.message}</p>}
                  </div>

                  <div>
                    <label className="font-semibold">Summary</label>
                    <Textarea rows={4} {...register("summary")} />
                    {errors.summary && <p className="text-red-500 text-sm">{errors.summary.message}</p>}
                  </div>
                </motion.div>
              )}

              {/* ---------------- Step 2 ---------------- */}
              {step === 2 && (
                <motion.div initial={{ x: 20, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="space-y-4">
                  <div>
                    <label className="font-semibold">Full Proposal</label>
                    <Textarea rows={6} {...register("proposal")} />
                    {errors.proposal && <p className="text-red-500 text-sm">{errors.proposal.message}</p>}
                  </div>
                </motion.div>
              )}

              {/* ---------------- Step 3 ---------------- */}
              {step === 3 && (
                <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="space-y-4">
                  <div>
                    <label className="font-semibold">Your Name</label>
                    <Input {...register("author")} />
                    {errors.author && <p className="text-red-500 text-sm">{errors.author.message}</p>}
                  </div>

                  <div>
                    <label className="font-semibold">Email Address</label>
                    <Input {...register("email")} />
                    {errors.email && <p className="text-red-500 text-sm">{errors.email.message}</p>}
                  </div>
                </motion.div>
              )}

              {/* Navigation Buttons */}
              <div className="flex justify-between mt-8">
                {step > 1 ? (
                  <Button type="button" onClick={prevStep}>Back</Button>
                ) : (
                  <div />
                )}

                {step < 3 ? (
                  <Button type="button" onClick={nextStep}>Next</Button>
                ) : (
                  <Button type="submit">Submit Proposal</Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
